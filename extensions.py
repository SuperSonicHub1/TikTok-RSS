"""rfeed extensions that implement https://blog.feedly.com/10-ways-to-optimize-your-feed-for-feedly/."""
from rfeed import Serializable, Extension

class MediaContent(Extension):
    def get_namespace(self):
        return {
            "xmlns:content": "http://purl.org/rss/1.0/modules/content/",
            'xmlns:media': 'http://search.yahoo.com/mrss/',
        }

class MediaItem(Serializable):
    def __init__(self, url: str, type: str, medium: str, isDefault: bool = False):
        Serializable.__init__(self)
        self.url = url
        self.type = type
        self.medium = medium
        self.isDefault = isDefault

    def publish(self, handler):
        Serializable.publish(self, handler)
        self._write_element(
            "content:media",
            None,
            {
                "url": self.url,
                "medium": self.medium,
                "type": self.type,
                "isDefault": str(self.isDefault).lower(),
            }
        )

class Webfeeds(Extension):
    def get_namespace(self):
        return {'xmlns:webfeeds': 'http://webfeeds.org/rss/1.0'}

class WebfeedsIcon(Serializable):
    def __init__(self, url: str):
        Serializable.__init__(self)
        self.url = url

    def publish(self, handler):
        Serializable.publish(self, handler)
        self._write_element("webfeeds:icon", self.url)

class WebfeedsCover(Serializable):
    def __init__(self, url: str):
        Serializable.__init__(self)
        self.url = url
    
    def publish(self, handler):
        Serializable.publish(self, handler)
        self._write_element("webfeeds:cover", None, {'image': self.url})
