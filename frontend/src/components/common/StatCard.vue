<template>
  <v-card
    :class="['stat-card', { 'stat-card--loading': loading }]"
    :color="cardColor"
    :variant="cardVariant"
    :height="cardHeight"
  >
    <v-card-text class="pa-4">
      <div class="d-flex align-center justify-space-between">
        <div class="stat-content">
          <div class="stat-icon-container mb-2">
            <v-icon
              :icon="icon"
              :color="iconColor"
              :size="iconSize"
            />
          </div>
          
          <div class="stat-value mb-1">
            <span v-if="!loading" class="text-h4 font-weight-bold">
              {{ formattedValue }}
            </span>
            <v-skeleton-loader
              v-else
              type="text"
              width="60px"
              height="32px"
            />
          </div>
          
          <div class="stat-label">
            <span class="text-subtitle-2" :class="labelClass">
              {{ label }}
            </span>
          </div>
          
          <div v-if="subtitle" class="stat-subtitle mt-1">
            <span class="text-caption text-medium-emphasis">
              {{ subtitle }}
            </span>
          </div>
        </div>
        
        <div v-if="showTrend && trend" class="stat-trend">
          <v-chip
            :color="trendColor"
            size="small"
            variant="outlined"
          >
            <v-icon
              :icon="trendIcon"
              size="small"
              start
            />
            {{ Math.abs(trend) }}%
          </v-chip>
        </div>
      </div>
      
      <!-- 进度条 -->
      <div v-if="showProgress && maxValue" class="mt-3">
        <v-progress-linear
          :model-value="progressValue"
          :color="progressColor"
          height="6"
          rounded
        />
        <div class="d-flex justify-space-between mt-1">
          <span class="text-caption">{{ value }}</span>
          <span class="text-caption">{{ maxValue }}</span>
        </div>
      </div>
    </v-card-text>
    
    <v-card-actions v-if="$slots.actions" class="pa-2 pt-0">
      <slot name="actions" />
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  // 基本数据
  value: {
    type: [Number, String],
    required: true
  },
  label: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    required: true
  },
  
  // 样式配置
  cardColor: {
    type: String,
    default: 'surface'
  },
  cardVariant: {
    type: String,
    default: 'elevated'
  },
  cardHeight: {
    type: [String, Number],
    default: 'auto'
  },
  iconColor: {
    type: String,
    default: 'primary'
  },
  iconSize: {
    type: [String, Number],
    default: 32
  },
  labelClass: {
    type: String,
    default: ''
  },
  
  // 格式化选项
  valueType: {
    type: String,
    default: 'number', // 'number', 'percentage', 'currency'
    validator: value => ['number', 'percentage', 'currency'].includes(value)
  },
  precision: {
    type: Number,
    default: 0
  },
  
  // 趋势显示
  showTrend: {
    type: Boolean,
    default: false
  },
  trend: {
    type: Number,
    default: 0 // 正数表示上升，负数表示下降
  },
  
  // 进度条
  showProgress: {
    type: Boolean,
    default: false
  },
  maxValue: {
    type: Number,
    default: 0
  },
  progressColor: {
    type: String,
    default: 'primary'
  },
  
  // 加载状态
  loading: {
    type: Boolean,
    default: false
  }
})

const formattedValue = computed(() => {
  if (typeof props.value === 'string') {
    return props.value
  }
  
  const numValue = Number(props.value)
  
  switch (props.valueType) {
    case 'percentage':
      return `${numValue.toFixed(props.precision)}%`
    case 'currency':
      return `¥${numValue.toLocaleString('zh-CN', { 
        minimumFractionDigits: props.precision,
        maximumFractionDigits: props.precision 
      })}`
    case 'number':
    default:
      return numValue.toLocaleString('zh-CN', {
        minimumFractionDigits: props.precision,
        maximumFractionDigits: props.precision
      })
  }
})

const progressValue = computed(() => {
  if (!props.maxValue) return 0
  return Math.min((Number(props.value) / props.maxValue) * 100, 100)
})

const trendColor = computed(() => {
  if (props.trend > 0) return 'success'
  if (props.trend < 0) return 'error'
  return 'grey'
})

const trendIcon = computed(() => {
  if (props.trend > 0) return 'mdi-trending-up'
  if (props.trend < 0) return 'mdi-trending-down'
  return 'mdi-trending-neutral'
})
</script>

<style scoped>
.stat-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-card--loading {
  opacity: 0.7;
}

.stat-icon-container {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: rgba(var(--v-theme-primary), 0.1);
  border-radius: 12px;
}

.stat-value {
  line-height: 1.2;
}

.stat-label {
  line-height: 1.3;
}

.stat-subtitle {
  line-height: 1.2;
}

.stat-trend {
  flex-shrink: 0;
}
</style>
