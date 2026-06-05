<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <el-container class="layout">
    <el-header height="56px" class="header">
      <span class="logo">CryptoLab</span>
      <nav class="nav">
        <RouterLink to="/symmetric">对称加密</RouterLink>
        <RouterLink to="/hash">哈希</RouterLink>
        <RouterLink to="/encoding">编码</RouterLink>
        <RouterLink to="/pubkey">公钥</RouterLink>
        <RouterLink to="/demos">漏洞演示</RouterLink>
      </nav>
    </el-header>
    <el-main>
      <RouterView />
    </el-main>
  </el-container>
</template>

<style scoped>
.layout { min-height: 100vh; }
.header { display: flex; align-items: center; gap: 24px; border-bottom: 1px solid #eee; }
.logo { font-weight: 700; font-size: 18px; }
.nav { display: flex; gap: 16px; }
.nav a { color: #555; text-decoration: none; }
.nav a.router-link-active { color: #409eff; font-weight: 600; }
</style>
