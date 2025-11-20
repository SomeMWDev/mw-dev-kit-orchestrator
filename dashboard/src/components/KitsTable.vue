<script setup lang="ts">
import {CdxTable} from "@wikimedia/codex";
import {onMounted, ref} from "vue";
import axios from "axios";

const kits = ref([])

onMounted(async () => {
  // TODO change URL to /api/kits
  const res = await axios.get("http://wikis.localhost/api/kits")
  kits.value = Object.values(res.data)
})
</script>

<template>
  <cdx-table
      caption="Dev Kits"
      :columns="[
          { id: 'name', label: 'Name' },
          { id: 'domain', label: 'Domain' },
          { id: 'port', label: 'Port' },
          { id: 'web_container', label: 'Web Container' },
          { id: 'status', label: 'Status' },
      ]"
      :data="kits"
      :use-row-headers="true"
  >
    <template #item-domain="{ item }">
      <a :href="`http://${item}`" target="_blank" rel="nofollow noreferrer">{{item}}</a>
    </template>
  </cdx-table>
</template>

<style scoped>

</style>
