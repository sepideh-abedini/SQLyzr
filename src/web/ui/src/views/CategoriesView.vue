<template>
  <div class="card">
    <TreeTable :value="categories" tableStyle="min-width: 50rem">
      <Column field="category" header="Category" expander style="width: 5%" />
      <Column field="subcategory" header="Subcategory" style="width: 5%" />
      <Column field="definition" header="Definition" style="width: 50%" />
    </TreeTable>
  </div>
</template>

<script>
import { TreeTable } from 'primevue'
import Column from 'primevue/column'
import categories from '@/data/categories.json'

export default {
  components: {
    TreeTable,
    Column,
  },
  name: 'CategoriesView',
  data() {
    return {
      categories: categories,
    }
  },
}
</script>
