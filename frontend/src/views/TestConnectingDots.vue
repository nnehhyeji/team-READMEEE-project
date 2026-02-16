      <script setup>
      import { ref, onMounted } from 'vue';
      import ConnectingDots from '../components/ConnectingDots.vue';
      
      // Mock data: 92 days (Max Q3/4 length)
      const demoRecords = ref(new Array(92).fill(false));
      
      const toggleRecord = (index) => {
          demoRecords.value[index] = !demoRecords.value[index];
      };
      
      const fillAll = () => {
          demoRecords.value = demoRecords.value.map(() => true);
      };
      
      const resetAll = () => {
          demoRecords.value = demoRecords.value.map(() => false);
      };
      
      const fillRandom = () => {
          demoRecords.value = demoRecords.value.map(() => Math.random() > 0.5);
      };
      
      onMounted(() => {
          // Initial pattern for demo
          // demoRecords.value[0] = true;
          // demoRecords.value[1] = true; 
          // demoRecords.value[3] = true;
      });
      </script>

<template>
  <div class="min-h-screen flex flex-col items-center p-8 bg-gray-100">
    <h1 class="text-3xl font-bold mb-6 text-gray-800">Connecting Dots Test</h1>
    
    <div class="mb-4 space-x-4">
      <button @click="fillAll" class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">Complete All</button>
      <button @click="resetAll" class="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600">Reset</button>
      <button @click="fillRandom" class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600">Random Fill</button>
    </div>

    <div class="w-full max-w-5xl h-[800px] border shadow-xl rounded-xl overflow-hidden">
      <ConnectingDots 
        :records="demoRecords"
        @toggle-dot="toggleRecord" 
      />
    </div>

    <div class="mt-8 text-gray-600">
      <p>Click on any dot to toggle its 'posted' state.</p>
      <ul class="list-disc ml-5 mt-2">
        <li><span class="text-[#000000] font-bold">Black</span>: Inactive (No record)</li>
        <li><span class="text-[#CC6F73] font-bold">Red</span>: Single (Record today, no record yesterday)</li>
        <li><span class="text-[#6193B6] font-bold">Blue</span>: Streak (Record today & yesterday)</li>
      </ul>
    </div>
  </div>
</template>

