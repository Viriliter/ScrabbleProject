from abc import ABC, abstractmethod
from typing import List, Optional

class Subject:
    def __init__(self):
        self._observers: List[Observer] = []

    def attach(self, observer: 'Observer'):
        """Attach an observer to the subject."""
        if observer not in self._observers:
            observer.set_subject(self)
            self._observers.append(observer)
            observer.listen(self)  # Allow observer to listen to the subject

    def detach(self, observer: 'Observer') -> None:
        """Detach an observer from the subject."""
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, observer: 'Observer', message: any) -> None:
        """Notify specific observer."""
        if observer in self._observers:
            observer.listen(message)
            return

    def notify_all(self, message: any) -> None:
        """Notify all observers."""
        for observer in self._observers:
            observer.listen(message)


class Observer(ABC):
    def __init__(self):
        self._subject: Subject = None
        self.__lock = False

    def set_subject(self, subject: Subject) -> None:
        """Set the subject of the observer."""
        self._subject = subject

    def emit(self, function_name: str, *args) -> Optional[any]:
        """Dynamically call the function of the subject."""
        if self._subject:
            # Dynamically call the method by its name
            method = getattr(self._subject, function_name, None)
            if callable(method):
                try:
                    return method(*args)
                except Exception as e:
                    print(f"Error: {e}")
            else:
                print(f"Function {function_name} not found in subject.")
        else:
            print("Subject is not set for this observer.")

    def listen(self, message: any) -> None:
        """Listen to notifications from the subject."""
        if self.__lock: return
        else: self._listen(message)
    
    @abstractmethod
    def _listen(self, message: any) -> None:
        """Listen to notifications from the subject."""
        pass
    
    def lock(self) -> None:
        """Locks the observer."""
        self.__lock = True
    
    def unlock(self) -> None:
        """Unlocks the observer."""
        self.__lock = False