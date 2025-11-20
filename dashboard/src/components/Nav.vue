<script setup lang="ts">

import {cdxIconCode} from "@wikimedia/codex-icons";
import {CdxIcon} from "@wikimedia/codex";
</script>

<template>
  <div class="nav">
    <h1>mw-dev-kit</h1>
    <a href="https://github.com/SomeMWDev/mw-dev-kit-orchestrator/" target="_blank" rel="noopener noreferrer">
      <cdx-icon :icon="cdxIconCode"/>
      Github
    </a>
  </div>
</template>

<style scoped lang="less">
@import ( reference ) '@wikimedia/codex-design-tokens/theme-wikimedia-ui.less';

.nav {
  display: flex;
  padding: @spacing-0 @spacing-125;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: @spacing-0;
  border-bottom: @border-subtle;
}

a {
  text-decoration: @text-decoration-none;
  color: currentColor;
}

a:hover,
a:hover .cdx-icon {
  color: @color-base--hover;
}
</style>
