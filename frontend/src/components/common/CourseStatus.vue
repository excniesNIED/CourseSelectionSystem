<template>
  <v-chip
    :color="statusColor"
    :variant="statusVariant"
    :size="size"
    class="status-chip"
  >
    <v-icon v-if="showIcon" start :size="iconSize">{{ statusIcon }}</v-icon>
    {{ statusText }}
  </v-chip>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  currentStudents: {
    type: Number,
    default: 0
  },
  maxStudents: {
    type: Number,
    default: 0
  },
  available: {
    type: Boolean,
    default: true
  },
  status: {
    type: String,
    default: 'open' // 'open', 'full', 'closed', 'cancelled'
  },
  showIcon: {
    type: Boolean,
    default: true
  },
  showNumbers: {
    type: Boolean,
    default: true
  },
  size: {
    type: String,
    default: 'small'
  }
})

const statusColor = computed(() => {
  switch (props.status) {
    case 'full':
      return 'error'
    case 'closed':
      return 'warning'
    case 'cancelled':
      return 'grey'
    case 'open':
    default:
      if (props.currentStudents >= props.maxStudents) {
        return 'error'
      } else if (props.currentStudents / props.maxStudents >= 0.8) {
        return 'warning'
      } else {
        return 'success'
      }
  }
})

const statusVariant = computed(() => {
  return props.status === 'cancelled' ? 'outlined' : 'elevated'
})

const statusText = computed(() => {
  switch (props.status) {
    case 'full':
      return '已满'
    case 'closed':
      return '已关闭'
    case 'cancelled':
      return '已取消'
    case 'open':
    default:
      if (props.showNumbers) {
        return `${props.currentStudents}/${props.maxStudents}`
      } else {
        if (props.currentStudents >= props.maxStudents) {
          return '已满'
        } else {
          return '可选'
        }
      }
  }
})

const statusIcon = computed(() => {
  switch (props.status) {
    case 'full':
      return 'mdi-account-off'
    case 'closed':
      return 'mdi-lock'
    case 'cancelled':
      return 'mdi-cancel'
    case 'open':
    default:
      if (props.currentStudents >= props.maxStudents) {
        return 'mdi-account-off'
      } else {
        return 'mdi-account-check'
      }
  }
})

const iconSize = computed(() => {
  switch (props.size) {
    case 'large':
      return 'default'
    case 'small':
    default:
      return 'small'
  }
})
</script>

<style scoped>
.status-chip {
  font-weight: 500;
}
</style>
