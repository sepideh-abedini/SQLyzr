<template>
  <div class="card trs mt-3 p-4">
    <Toast position="bottom-right" />

    <h1 class="text-3xl font-bold mb-6">Evaluation Metrics</h1>

    <Tabs value="0" scrollable>
      <TabList>
        <Tab value="0"><h2>EA</h2></Tab>
        <Tab value="1"><h2>EM</h2></Tab>
        <Tab value="2"><h2>REA</h2></Tab>
        <Tab value="3"><h2>TU</h2></Tab>
        <Tab value="4"><h2>CC</h2></Tab>
        <Tab value="5"><h2>ETC</h2></Tab>
      </TabList>

      <TabPanels>
        <TabPanel value="0">
          <h2 class="text-xl font-semibold mb-2">Execution Accuracy (EA)</h2>
          <p>
            This metric assesses whether the execution result of the predicted query is equal to the
            execution result of the gold query on a single database instance.
          </p>
        </TabPanel>

        <TabPanel value="1">
          <h2 class="text-xl font-semibold mb-2">Exact Match (EM)</h2>
          <p>
            Exact Match (EM) checks whether the structural components of a predicted SQL query are
            equivalent to those of the gold query, following the definition introduced in the
            Spider benchmark. EM performs set-based comparison over query components
            and therefore tolerates variations within a component, such as different column
            orderings in the SELECT clause.
          </p>
        </TabPanel>

        <TabPanel value="2">
          <h2 class="text-xl font-semibold mb-2">Relaxed Execution Accuracy (REA)</h2>
          <p>
            Relaxed Execution Accuracy (REA) is a new metric provided by SQLyzr to mitigate the
            restrictiveness of EA. REA is designed to account for near-correct predictions whose
            execution results differ from the gold query only due to minor errors, such as column
            ordering or extra columns. To compute REA, the predicted query is first normalized and
            then compared against the gold query under a relaxed equivalence relation which ignores
            minor deviations like column ordering.
          </p>
        </TabPanel>

        <TabPanel value="3">
          <h2 class="text-xl font-semibold mb-2">Token Usage (TU)</h2>
          <p>
            Large language models encode both input and output sequences as tokens, and generation
            cost is typically proportional to the number of tokens consumed. Therefore, token usage
            can be used for estimating the generation cost of language-model-based text-to-SQL systems.
          </p>
        </TabPanel>

        <TabPanel value="4">
          <h2 class="text-xl font-semibold mb-2">Complexity Consistency (CC)</h2>
          <p>
            Complexity Consistency (CC) measures whether the predicted query introduces additional
            structural complexity compared to the gold query.
          </p>
        </TabPanel>

        <TabPanel value="5">
          <h2 class="text-xl font-semibold mb-2">Execution Time Consistency (ETC)</h2>
          <p>
            Execution Time Consistency (ETC) evaluates whether the predicted query executes within
            an acceptable relative time overhead compared to the gold query. While correctness ensures
            semantic validity, ETC captures the efficiency of the query.
          </p>
        </TabPanel>
      </TabPanels>
    </Tabs>
  </div>
</template>

<script setup>
import { Toast, Tabs, TabList, Tab, TabPanels, TabPanel } from 'primevue'
</script>

<style scoped>
.trs {
  max-width: 1000px;
  margin: 0 auto;
  line-height: 1.6;
}
code {
  background: #f4f4f4;
  padding: 2px 4px;
  border-radius: 4px;
}
</style>
