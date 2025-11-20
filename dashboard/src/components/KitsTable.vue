<script setup lang="ts">
import {CdxButton, CdxIcon, CdxInfoChip, CdxTable} from "@wikimedia/codex";
import {onMounted, ref} from "vue";
import axios from "axios";
import {cdxIconPlay, cdxIconReload, cdxIconStop} from "@wikimedia/codex-icons";

const kits = ref([])

onMounted(async () => {
  // TODO change URL to /api/kits
  const res = await axios.get("http://wikis.localhost/api/kits")
  kits.value = Object.values(res.data)
})

const getStatus = (status: string) => {
  switch (status) {
    case "running":
    case "healthy":
      return "success"
    case "created":
    case "restarting":
      return "notice"
    case "paused":
      return "warning"
    case "dead":
    case "exited":
      return "error"
  }
}
const capitalize = (str: string) => str.charAt(0).toUpperCase() + str.slice(1)

const start = (name: string) => {}
const stop = (name: string) => {}
const restart = (name: string) => {}
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
          { id: 'actions', label: 'Actions' },
      ]"
      :data="kits"
      :use-row-headers="true"
  >
    <template #item-domain="{ item }">
      <a :href="`http://${item}`" target="_blank" rel="nofollow noreferrer">{{item}}</a>
    </template>

    <template #item-status="{ item }">
      <cdx-info-chip :status="getStatus(item)">{{capitalize(item)}}</cdx-info-chip>
    </template>

    <template #item-actions="{ row }">
      <div>
        <cdx-button
            weight="quiet"
            aria-label="Start"
            @click="start( row.name )"
            action="progressive"
            v-if="row.status === 'exited'"
        ><cdx-icon :icon="cdxIconPlay" /></cdx-button>
        <cdx-button
            weight="quiet"
            aria-label="Stop"
            @click="stop( row.name )"
            action="destructive"
            v-if="row.status === 'running' || row.status === 'healthy'"
        ><cdx-icon :icon="cdxIconStop" /></cdx-button>
        <cdx-button
            weight="quiet"
            aria-label="Restart"
            @click="restart( row.name )"
            action="default"
            v-if="row.status === 'running' || row.status === 'healthy'"
        ><cdx-icon :icon="cdxIconReload" /></cdx-button>
      </div>
    </template>
  </cdx-table>
</template>

<style scoped>

</style>
