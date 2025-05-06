from flask import Flask

class BaseAPI:
    """Base class for all API classes"""
    
    def __init__(self, app: Flask, config_file: str):
        """
        Initialize the API class
        
        Args:
            app: Flask application instance
            config_file: Path to the configuration file
        """
        self.app = app
        self.config_file = config_file
        
    def register_routes(self):
        """
        Register routes with the Flask application.
        This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement register_routes method")