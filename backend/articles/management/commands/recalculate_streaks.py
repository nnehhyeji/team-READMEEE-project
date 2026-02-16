from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from articles.models import Article
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Recalculate consecutive_days and max_consecutive_days for ALL users based on article history'

    def handle(self, *args, **options):
        users = User.objects.all()
        total_users = users.count()
        self.stdout.write(f"🔍 Found {total_users} users. Starting recalculation...")

        updated_count = 0

        for user in users:
            # Fetch distinct dates for this user's articles
            articles = Article.objects.filter(author=user).order_by('created_at')
            dates = sorted(list(set(a.created_at.date() for a in articles)))

            if not dates:
                if user.consecutive_days != 0:
                    user.consecutive_days = 0
                    user.save()
                    self.stdout.write(f"   👤 {user.username}: No articles. Reset to 0.")
                continue

            # 1. Calculate Max Streak
            max_streak = 0
            current_temp_streak = 0
            prev_date = None

            for d in dates:
                if prev_date is None:
                    current_temp_streak = 1
                else:
                    if d == prev_date + timedelta(days=1):
                        current_temp_streak += 1
                    else:
                        current_temp_streak = 1
                
                if current_temp_streak > max_streak:
                    max_streak = current_temp_streak
                prev_date = d

            # 2. Calculate Current Streak (ending at the latest post)
            # Logic: Count backwards from the last post date using the *available dates* list
            
            latest_date = dates[-1]
            current_streak = 1
            
            # Loop backwards from the second to last item
            for i in range(len(dates) - 2, -1, -1):
                d = dates[i]
                expected_date = latest_date - timedelta(days=current_streak)
                if d == expected_date:
                    current_streak += 1
                else:
                    break
            
            # NOTE: If we want "Current Streak" to be 0 if they haven't posted recently (e.g. within yesterday),
            # we should add a check here. However, typical "game" logic sometimes preserves the badge number 
            # until they log in and break it, or strictly resets it.
            # For "DayLog" context, if they missed yesterday, it technically broke.
            # let's stick to the "streak ending at the last post" for now as it's safe for dummy data visuals.
            # If we wanted strict "live" streak:
            # today = timezone.localdate()
            # if latest_date < today - timedelta(days=1):
            #    current_streak = 0
            
            # Update user
            user.consecutive_days = current_streak
            # Only update max if calculated max is higher (or trust the calculation fully? Let's trust calc)
            user.max_consecutive_days = max(user.max_consecutive_days, max_streak)
            
            user.save()
            updated_count += 1
            self.stdout.write(f"   ✅ {user.username}: Streak={current_streak}, Max={user.max_consecutive_days}")

        self.stdout.write(self.style.SUCCESS(f"\n🎉 Successfully recalculated streaks for {updated_count} users."))
