import unittest
from zuu.decorcls_Singleton import singleton_factory

class TestSingletonFactory(unittest.TestCase):
    def test_basic_singleton(self):
        # Test basic singleton without by_var
        @singleton_factory
        class BasicSingleton:
            def __init__(self, value=None):
                self.value = value

        # Create instances and verify they're the same
        instance1 = BasicSingleton(1)
        instance2 = BasicSingleton(2)
        
        self.assertIs(instance1, instance2)
        self.assertEqual(instance1.value, instance2.value)
        self.assertEqual(instance1.value, 1)  # First initialization value should stick

    def test_parameterized_singleton(self):
        # Test singleton with by_var parameter
        @singleton_factory(by_var='name')
        class NamedSingleton:
            def __init__(self, name, value=None):
                self.name = name
                self.value = value

        # Create instances with different names
        instance1 = NamedSingleton('a', value=1)
        instance2 = NamedSingleton('b', value=2)
        instance3 = NamedSingleton('a', value=3)  # Should return existing 'a' instance

        # Different names should create different instances
        self.assertIsNot(instance1, instance2)
        
        # Same name should return same instance
        self.assertIs(instance1, instance3)
        
        # Values should persist from first initialization
        self.assertEqual(instance1.value, 1)
        self.assertEqual(instance2.value, 2)
        self.assertEqual(instance3.value, 1)  # Same as instance1

    def test_kwargs_singleton(self):
        # Test singleton with by_var using kwargs
        @singleton_factory(by_var='id')
        class KwargsSingleton:
            def __init__(self, id, value=None):
                self.id = id
                self.value = value

        # Create instances using kwargs
        instance1 = KwargsSingleton(id='x', value=1)
        instance2 = KwargsSingleton(id='x', value=2)

        self.assertIs(instance1, instance2)
        self.assertEqual(instance1.value, 1)  # First value should persist

    def test_empty_initialization(self):
        # Test handling of empty initialization
        @singleton_factory(by_var='name')
        class EmptySingleton:
            def __init__(self):
                pass

        # Should raise TypeError when no arguments provided
        with self.assertRaises(TypeError):
            EmptySingleton()

if __name__ == '__main__':
    unittest.main() 