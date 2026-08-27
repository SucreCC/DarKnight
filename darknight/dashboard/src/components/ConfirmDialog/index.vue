<script setup lang="ts">
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle
} from '@/components/ui/alert-dialog'
import { confirmState, resolveConfirm } from '@/composables/useConfirm'
</script>

<template>
  <AlertDialog :open="confirmState.open" @update:open="(v: boolean) => !v && resolveConfirm(false)">
    <AlertDialogContent>
      <AlertDialogHeader>
        <AlertDialogTitle>{{ confirmState.options.title }}</AlertDialogTitle>
        <AlertDialogDescription>{{ confirmState.options.description }}</AlertDialogDescription>
      </AlertDialogHeader>
      <AlertDialogFooter>
        <AlertDialogCancel @click="resolveConfirm(false)">
          {{ confirmState.options.cancelText }}
        </AlertDialogCancel>
        <AlertDialogAction
          :class="
            confirmState.options.destructive
              ? 'bg-destructive text-destructive-foreground hover:bg-destructive/90'
              : ''
          "
          @click="resolveConfirm(true)"
        >
          {{ confirmState.options.confirmText }}
        </AlertDialogAction>
      </AlertDialogFooter>
    </AlertDialogContent>
  </AlertDialog>
</template>
