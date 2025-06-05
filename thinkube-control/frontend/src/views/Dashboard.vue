<!-- src/views/Dashboard.vue -->
<template>
  <div>
    <NavBar 
      :categories="categories" 
      :user="user" 
      @filter-category="filterByCategory" 
    />
    
    <div class="container mx-auto px-4 py-8">
      <h1 class="text-3xl font-bold mb-2">Dashboard Hub</h1>
      <p class="mb-8">Your unified portal to K8s platform services</p>
      
      <div v-if="loading" class="flex justify-center">
        <span class="loading loading-spinner loading-lg"></span>
      </div>
      
      <div v-else>
        <div class="flex items-center mb-6 flex-wrap gap-2">
          <button 
            class="btn btn-sm" 
            :class="{ 'btn-primary': !selectedCategory }" 
            @click="selectedCategory = null"
          >
            All
          </button>
          
          <button 
            v-for="category in categories" 
            :key="category"
            class="btn btn-sm" 
            :class="{ 'btn-primary': selectedCategory === category }"
            @click="filterByCategory(category)"
          >
            {{ capitalizeFirst(category) }}
          </button>
        </div>
        
        <div v-if="filteredDashboards.length === 0" class="alert alert-info">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <span>No dashboards available for the selected category.</span>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <DashboardCard 
            v-for="dashboard in filteredDashboards" 
            :key="dashboard.id" 
            :dashboard="dashboard" 
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue';
import DashboardCard from '@/components/DashboardCard.vue';
import { getDashboards, getDashboardCategories } from '@/services/api';
import { getUserInfo } from '@/services/auth';

export default {
  name: 'DashboardView',
  components: {
    NavBar,
    DashboardCard
  },
  data() {
    return {
      dashboards: [],
      categories: [],
      selectedCategory: null,
      loading: true,
      user: {
        preferred_username: 'Loading...',
        email: '',
        roles: []
      }
    };
  },
  computed: {
    filteredDashboards() {
      if (!this.selectedCategory) {
        return this.dashboards;
      }
      
      return this.dashboards.filter(dashboard => dashboard.category === this.selectedCategory);
    }
  },
  async created() {
    try {
      // Get user info (now comes from OAuth2 Proxy via backend)
      this.user = await getUserInfo();
      
      // Get dashboards and categories
      const [dashboards, categories] = await Promise.all([
        getDashboards(),
        getDashboardCategories()
      ]);
      
      this.dashboards = dashboards;
      this.categories = categories;
    } catch (error) {
      console.error('Failed to load dashboard data', error);
      // Show error toast or notification
    } finally {
      this.loading = false;
    }
  },
  methods: {
    capitalizeFirst(str) {
      return str.charAt(0).toUpperCase() + str.slice(1);
    },
    filterByCategory(category) {
      this.selectedCategory = category;
    }
  }
}
</script>