<template>
  <v-card class="ma-4">
    <v-card-title class="d-flex justify-space-between align-center">
      <span class="text-h5">{{ title }}</span>
      <v-btn
        color="primary"
        @click="$emit('add-item')"
        prepend-icon="mdi-plus"
        variant="elevated"
      >
        新增
      </v-btn>
    </v-card-title>

    <v-card-text>
      <!-- 搜索栏 -->
      <v-text-field
        v-model="search"
        label="搜索"
        prepend-inner-icon="mdi-magnify"
        variant="outlined"
        clearable
        hide-details
        class="mb-4"
      />

      <!-- 数据表格 -->
      <v-data-table
        :headers="computedHeaders"
        :items="items"
        :loading="loading"
        :search="search"
        class="elevation-1"
        :items-per-page="10"
        :items-per-page-options="[5, 10, 25, 50]"
        show-current-page
      >
        <!-- 自定义列插槽 -->
        <template
          v-for="header in headers"
          :key="header.key"
          v-slot:[`item.${header.key}`]="{ item }"
        >
          <slot
            :name="`item.${header.key}`"
            :item="item"
            :value="item[header.key]"
          >
            {{ item[header.key] }}
          </slot>
        </template>

        <!-- 操作列 -->
        <template v-slot:item.actions="{ item }">
          <v-tooltip text="编辑">
            <template v-slot:activator="{ props }">
              <v-btn
                v-bind="props"
                icon="mdi-pencil"
                size="small"
                color="primary"
                variant="text"
                @click="$emit('edit-item', item)"
              />
            </template>
          </v-tooltip>

          <v-tooltip text="删除">
            <template v-slot:activator="{ props }">
              <v-btn
                v-bind="props"
                icon="mdi-delete"
                size="small"
                color="error"
                variant="text"
                @click="$emit('delete-item', item)"
              />
            </template>
          </v-tooltip>

          <!-- 自定义操作按钮插槽 -->
          <slot name="custom-actions" :item="item" />
        </template>

        <!-- 加载状态 -->
        <template v-slot:loading>
          <v-skeleton-loader type="table-row@10" />
        </template>

        <!-- 无数据状态 -->
        <template v-slot:no-data>
          <v-empty-state
            headline="暂无数据"
            title="还没有任何数据"
            text="点击新增按钮添加第一条数据"
            icon="mdi-database-outline"
          />
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  name: 'CrudDataTable',
  props: {
    title: {
      type: String,
      required: true,
      default: '数据管理'
    },
    headers: {
      type: Array,
      required: true,
      default: () => []
    },
    items: {
      type: Array,
      required: true,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    showActions: {
      type: Boolean,
      default: true
    }
  },
  emits: ['add-item', 'edit-item', 'delete-item'],
  data() {
    return {
      search: ''
    }
  },
  computed: {
    computedHeaders() {
      const headers = [...this.headers]
      
      // 如果需要显示操作列，添加操作列
      if (this.showActions) {
        headers.push({
          title: '操作',
          key: 'actions',
          sortable: false,
          width: 120
        })
      }
      
      return headers
    }
  }
}
</script>

<style scoped>
.v-card-title {
  background-color: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
}

.v-data-table {
  border-radius: 8px;
}

.v-btn {
  margin: 0 2px;
}
</style>
