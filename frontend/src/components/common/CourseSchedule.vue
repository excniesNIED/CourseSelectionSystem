<template>
  <div class="course-schedule">
    <v-chip
      v-if="hasSchedule"
      :color="chipColor"
      :variant="chipVariant"
      size="small"
      class="schedule-chip"
    >
      <v-icon v-if="showIcon" start size="small">{{ scheduleIcon }}</v-icon>
      {{ formattedSchedule }}
    </v-chip>
    <v-chip
      v-else
      color="grey"
      variant="outlined"
      size="small"
    >
      <v-icon start size="small">mdi-clock-outline</v-icon>
      未安排
    </v-chip>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  dayOfWeek: {
    type: Number,
    default: null
  },
  startTime: {
    type: String,
    default: ''
  },
  endTime: {
    type: String,
    default: ''
  },
  location: {
    type: String,
    default: ''
  },
  showIcon: {
    type: Boolean,
    default: true
  },
  showLocation: {
    type: Boolean,
    default: false
  },
  compact: {
    type: Boolean,
    default: false
  },
  chipColor: {
    type: String,
    default: 'primary'
  },
  chipVariant: {
    type: String,
    default: 'elevated'
  }
})

const weekDays = ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日']

const hasSchedule = computed(() => {
  return props.dayOfWeek && props.startTime && props.endTime
})

const formattedSchedule = computed(() => {
  if (!hasSchedule.value) {
    return '未安排'
  }
  
  const dayName = weekDays[props.dayOfWeek] || '未知'
  let schedule = props.compact 
    ? `${dayName} ${props.startTime}-${props.endTime}`
    : `${dayName} ${props.startTime}-${props.endTime}`
  
  if (props.showLocation && props.location) {
    schedule += ` @ ${props.location}`
  }
  
  return schedule
})

const scheduleIcon = computed(() => {
  if (!hasSchedule.value) {
    return 'mdi-clock-outline'
  }
  return 'mdi-clock'
})
</script>

<style scoped>
.course-schedule {
  display: inline-block;
}

.schedule-chip {
  font-weight: 500;
}
</style>
