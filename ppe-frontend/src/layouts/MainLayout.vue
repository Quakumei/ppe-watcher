<!-- src/layouts/MainLayout.vue -->
<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-toolbar-title>PPE Safety Monitoring</q-toolbar-title>
        <q-btn flat label="Dashboard" to="/dashboard" />
        <q-btn flat label="Cameras" to="/cameras" />
        <q-btn flat label="Events" to="/events" />
        <!-- Можно добавить кнопку для экспорта, если потребуется -->
      </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view :key="$route.fullPath" />
    </q-page-container>
  </q-layout>
</template>

<script setup>
</script>
