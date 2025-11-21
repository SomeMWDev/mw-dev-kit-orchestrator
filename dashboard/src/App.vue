<script setup lang="ts">
import Home from "./components/Home.vue";
import {type Component, computed, ref} from "vue";
import NotFound from "./components/NotFound.vue";
import Nav from "./components/Nav.vue";

const routes: Record<string, Component> = {
  '/': Home,
	'test': Home,
}

const currentPath = ref(window.location.hash)

window.addEventListener('hashchange', () => {
  currentPath.value = window.location.hash
})

const currentView = computed(() => {
  return routes[currentPath.value.slice(1) || '/'] || NotFound;
})
</script>

<template>
  <Nav />
  <div id="content">
    <component :is="currentView" />
  </div>
</template>

<style scoped>
</style>
