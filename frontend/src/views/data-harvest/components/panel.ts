import { ref, nextTick } from "vue";

export const update = ref(false);

export const handleUpdate = () => {
  update.value = true;
  nextTick(() => {
    update.value = false;
  });
};
