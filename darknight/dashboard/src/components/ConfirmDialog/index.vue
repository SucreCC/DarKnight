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

function onOpenUpdate(open: boolean) {
  if (!open) resolveConfirm(false)
}

function onConfirmClick(event: Event) {
  // Capture + prevent so this runs before Reka DialogClose's bubble-phase
  // onOpenChange(false). Otherwise overlay-close rejects pending first and
  // the confirm click becomes a no-op. resolveConfirm already closes the dialog.
  event.preventDefault()
  resolveConfirm(true)
}
</script>

<template>
  <AlertDialog :open="confirmState.open" @update:open="onOpenUpdate">
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
          @click.capture.prevent="onConfirmClick"
        >
          {{ confirmState.options.confirmText }}
        </AlertDialogAction>
      </AlertDialogFooter>
    </AlertDialogContent>
  </AlertDialog>
</template>
