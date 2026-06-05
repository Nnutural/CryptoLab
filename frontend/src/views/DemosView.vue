<script setup lang="ts">
// TODO: 4 demo cards: ECB image leak / ECDSA k-reuse / RSA low-exp / PBKDF2 impact
</script>

<template>
  <el-card>
    <template #header>漏洞演示</template>
    <el-alert type="warning" :closable="false" show-icon>
      教学演示用途；以下端点故意保留漏洞，请勿在生产环境中使用。
    </el-alert>
    <el-empty description="占位 — 待算法实现后接通 UI" />
  </el-card>
</template>
