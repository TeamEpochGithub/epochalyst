from typing import Any

from agogos.training import TrainingSystem, TrainType

from epochalyst._core._caching._cacher import _CacheArgs, _Cacher
from epochalyst._core._logging._logger import _Logger


class TrainingPipeline(TrainingSystem, _Cacher, _Logger):
    """The training pipeline. This is the class used to create the pipeline for the training of the model.

    :param steps: The steps to train the model.
    """

    def train(
        self,
        x: Any,
        y: Any,
        cache_args: _CacheArgs | None = None,
        **train_args: Any,
    ) -> tuple[Any, Any]:
        """Train the system.

        :param x: The input to the system.
        :param y: The expected output of the system.
        :return: The input and output of the system.
        """
        if cache_args and self._cache_exists(name=self.get_hash() + "x", cache_args=cache_args) and self._cache_exists(name=self.get_hash() + "y", cache_args=cache_args):
            self.log_to_terminal(
                f"Cache exists for training pipeline with hash: {self.get_hash()}. Using the cache.",
            )
            x = self._get_cache(name=self.get_hash() + "x", cache_args=cache_args)
            y = self._get_cache(name=self.get_hash() + "y", cache_args=cache_args)
            return x, y

        if self.get_steps():
            self.log_section_separator("Training Pipeline")

        self.all_steps = self.get_steps()

        # Furthest step
        for i, step in enumerate(self.get_steps()):
            # Check if step is instance of _Cacher and if cache_args exists
            if not isinstance(step, _Cacher) or not isinstance(step, TrainType):
                self.log_to_debug(f"{step} is not instance of _Cacher or TrainType")
                continue

            step_args = train_args.get(step.__class__.__name__, None)
            if step_args is None:
                self.log_to_debug(f"{step} is not given train_args")
                continue

            step_cache_args = step_args.get("cache_args", None)
            if step_cache_args is None:
                self.log_to_debug(f"{step} is not given cache_args")
                continue

            step_cache_exists = step._cache_exists(
                step.get_hash() + "x",
                step_cache_args,
            ) and step._cache_exists(step.get_hash() + "y", step_cache_args)
            if step_cache_exists:
                self.log_to_debug(
                    f"Cache exists for {step}, moving index of steps to {i}",
                )
                self.steps = self.all_steps[i:]

        x, y = super().train(x, y, **train_args)

        if cache_args:
            self._store_cache(name=self.get_hash() + "x", data=x, cache_args=cache_args)
            self._store_cache(name=self.get_hash() + "y", data=y, cache_args=cache_args)

        # Set steps to original in case class is called again (case: train -> predict)
        self.steps = self.all_steps

        return x, y

    def predict(
        self,
        x: Any,
        cache_args: _CacheArgs | None = None,
        **pred_args: Any,
    ) -> Any:
        """Predict the output of the system.

        :param x: The input to the system.
        :param cache_args: The cache arguments.
        :return: The output of the system.
        """
        if cache_args and self._cache_exists(self.get_hash() + "p", cache_args):
            return self._get_cache(self.get_hash() + "p", cache_args)

        if self.get_steps():
            self.log_section_separator("Prediction Pipeline")

        self.all_steps = self.get_steps()

        # Retrieve furthest step calculated
        for i, step in enumerate(self.get_steps()):
            # Check if step is instance of _Cacher and if cache_args exists
            if not isinstance(step, _Cacher) or not isinstance(step, TrainType):
                self.log_to_debug(f"{step} is not instance of _Cacher or TrainType")
                continue

            step_args = pred_args.get(step.__class__.__name__, None)
            if step_args is None:
                self.log_to_debug(f"{step} is not given train_args")
                continue

            step_cache_args = step_args.get("cache_args", None)
            if step_cache_args is None:
                self.log_to_debug(f"{step} is not given cache_args")
                continue

            step_cache_exists = step._cache_exists(
                step.get_hash() + "p",
                step_cache_args,
            )
            if step_cache_exists:
                self.log_to_debug(
                    f"Cache exists for {step}, moving index of steps to {i}",
                )
                self.steps = self.all_steps[i:]

        x = super().predict(x, **pred_args)

        self._store_cache(self.get_hash() + "p", x, cache_args) if cache_args else None

        # Set steps to original in case class is called again
        self.steps = self.all_steps

        return x
