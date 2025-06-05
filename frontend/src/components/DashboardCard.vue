<!-- src/components/DashboardCard.vue -->
<template>
  <div class="dashboard-card">
    <div class="card-body">
      <div class="flex items-center justify-between">
        <h2 class="card-title">{{ dashboard.name }}</h2>
        <div :class="'badge category-badge-' + dashboard.category">
          {{ capitalizeFirst(dashboard.category) }}
        </div>
      </div>
      
      <p>{{ dashboard.description }}</p>
      
      <div class="card-actions justify-end mt-4">
        <a :href="dashboard.url" target="_blank" rel="noopener noreferrer" class="btn btn-primary">
          <span class="mr-2">Open</span>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DashboardCard',
  props: {
    dashboard: {
      type: Object,
      required: true
    }
  },
  methods: {
    capitalizeFirst(str) {
      return str.charAt(0).toUpperCase() + str.slice(1);
    }
  }
}
</script>