<!-- src/components/ProfileDropdown.vue -->
<template>
  <div class="dropdown dropdown-end">
    <label tabindex="0" class="btn btn-ghost btn-circle avatar">
      <div class="avatar placeholder">
        <div class="bg-neutral text-neutral-content rounded-full w-10">
          <span>{{ userInitials }}</span>
        </div>
      </div>
    </label>
    <ul tabindex="0" class="mt-3 z-[1] p-2 shadow menu menu-sm dropdown-content bg-base-100 rounded-box w-52">
      <li class="p-2 text-center font-medium">
        {{ user.preferred_username }}
        <span class="text-xs block text-base-content/70">{{ user.email }}</span>
      </li>
      <li v-if="user.roles && user.roles.length > 0" class="p-2">
        <div class="flex flex-wrap gap-1">
          <div v-for="role in user.roles" :key="role" class="badge badge-sm">
            {{ role }}
          </div>
        </div>
      </li>
      <div class="divider my-0"></div>
      <li><a @click="$emit('logout')">Logout</a></li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'ProfileDropdown',
  props: {
    user: {
      type: Object,
      required: true
    }
  },
  computed: {
    userInitials() {
      if (!this.user) return '?';
      
      if (this.user.name) {
        // Use the first letter of first and last name
        const nameParts = this.user.name.split(' ');
        if (nameParts.length > 1) {
          return `${nameParts[0][0]}${nameParts[nameParts.length - 1][0]}`.toUpperCase();
        }
        // Just use the first letter if only one name
        return this.user.name[0].toUpperCase();
      }
      
      // Fall back to the first letter of the username
      return this.user.preferred_username ? this.user.preferred_username[0].toUpperCase() : '?';
    }
  }
}
</script>