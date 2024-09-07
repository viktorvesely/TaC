from typing import Generator, Callable

type ContinueAnimating = bool

class Animation[T]:
    def __init__(
            self,
            generator: Generator[T, None, None],
            on_animation: Callable[[T], None] | None = None,
            on_finish: Callable[[], None] | None = None
        ):
        self.generator: Generator[T, None, None] = generator
        self.finished = False
        self.on_animation = on_animation
        self.on_finish = on_finish

    def __next__(self) -> tuple[T | None, ContinueAnimating]:

        if self.finished:
            raise StopIteration()

        try:
            val = next(self.generator)

            if callable(self.on_animation):
                self.on_animation(val)
            return val, True
        except StopIteration:

            if callable(self.on_finish):
                self.on_finish()

            self.finished = True
            return None, False

