<template>
  <div class="sql-diff-container">
    <div class="flex justify-content-between align-items-center mb-2">
      <h5 v-if="title">{{ title }}</h5>

      <div class="trs-item-content">
        <div class="trs-sql">
          <Tag severity="warn">Predicted SQL</Tag>
          <pre v-html="isDiffVisible ? calculateDiff(pred, gold) : highlightSQL(pred)"></pre>
        </div>
        <div class="trs-sql">
          <Tag>Gold SQL</Tag>
          <pre v-html="highlightSQL(gold)"></pre>
        </div>
      </div>
      <Button
        :label="isDiffVisible ? 'Hide Diff' : 'Show Diff'"
        :icon="isDiffVisible ? 'pi pi-eye-slash' : 'pi pi-eye'"
        @click="isDiffVisible = !isDiffVisible"
        class="p-button-sm p-button-text"
      />
    </div>
  </div>
</template>

<script>
import Button from 'primevue/button'
import * as DiffMatchPatch from 'diff-match-patch'
import Prism from 'prismjs'
import 'prismjs/components/prism-sql'
import 'prismjs/themes/prism.css'
import { Tag } from 'primevue'

export default {
  name: 'SQLDiff',
  components: { Button, Tag },
  props: {
    pred: { type: String, required: true },
    gold: { type: String, required: true },
    title: { type: String, default: '' },
    initialShowDiff: { type: Boolean, default: true },
  },
  data() {
    return {
      isDiffVisible: this.initialShowDiff,
      dmp: new DiffMatchPatch.diff_match_patch(),
    }
  },
  computed: {
    formattedSQL() {
      if (this.isDiffVisible) {
        return this.calculateDiff(this.pred, this.gold)
      }
      return this.highlightSQL(this.gold)
    },
  },
  methods: {
    highlightSQL(sql) {
      return Prism.highlight(sql, Prism.languages.sql, 'sql')
    },
    calculateDiff(base, target) {
      const diffs = this.dmp.diff_main(base, target)
      this.dmp.diff_cleanupSemantic(diffs)

      let html = ''
      for (let i = 0; i < diffs.length; i++) {
        const [op, text] = diffs[i]

        // Logical check for "Changed" (Deletion followed by Insertion)
        const isChange = i < diffs.length - 1 && op === -1 && diffs[i + 1][0] === 1

        if (isChange) {
          html += `<span class="diff-changed">${this.highlightSQL(text)}</span>`
          // Note: In a true side-by-side this is complex,
          // but for inline we treat the deletion as the 'change' marker.
        } else if (op === 1) {
          html += `<span class="diff-added">${this.highlightSQL(text)}</span>`
        } else if (op === -1) {
          html += `<span class="diff-removed">${this.highlightSQL(text)}</span>`
        } else {
          html += this.highlightSQL(text)
        }
      }
      return html
    },
  },
}
</script>

<style scoped>
.trs-sql pre {
  background-color: #f8f9fa;
  padding: 0.75rem;
  border-radius: 0.25rem;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
  font-family: monospace;
}

:deep(.diff-added) {
  background-color: #e6ffed;
  color: #22863a;
  border-radius: 2px;
}

:deep(.diff-removed) {
  background-color: #ffeef0;
  color: #cb2431;
  text-decoration: line-through;
  border-radius: 2px;
}

:deep(.diff-changed) {
  background-color: #e6f7ff;
  color: #0366d6;
  border-radius: 2px;
}
</style>
