from abc import ABC, abstractmethod
from typing import List, Optional
from threading import Thread, Lock

class Subject:
    """
    @brief Subject class representing a subject in the observer pattern.
    @note: This class allows observers to attach and detach themselves, and notifies them of changes.
    @param _observers: List of observers attached to the subject.
    @note: The observers are notified when the subject changes.
    """
    def __init__(self):
        self._observers: List[Observer] = []
        self._mutex = Lock()

    def attach(self, observer: 'Observer'):
        """Attach an observer to the subject."""
        if observer not in self._observers:
            observer.set_subject(self)
            self._observers.append(observer)

    def detach(self, observer: 'Observer') -> None:
        """Detach an observer from the subject."""
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, observer: 'Observer', message: any) -> None:
        """Notify specific observer."""
        if observer in self._observers:
            Thread(target=observer.listen, args=(message,), daemon=True).start()

    def notify_all(self, message: any) -> None:
        """Notify all observers."""
        for observer in self._observers:
            Thread(target=observer.listen, args=(message,), daemon=True).start()


class Observer(ABC):
    """
    @brief Observer class representing an observer in the observer pattern.
    @note: This class allows observers to listen to notifications from the subject.
    @param _subject: The subject that the observer is observing.
    @param __lock: A lock to prevent multiple notifications at the same time.
    """
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
                    self.lock()  # Prevents recursive calls
                    r = method(*args)
                    self.unlock()
                    return r
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