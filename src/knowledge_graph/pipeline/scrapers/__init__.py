"""Web scrapers for external data sources."""

from .thoughtworks_scraper import ThoughtWorksRadarScraper, scrape_fuzz_testing

__all__ = ["ThoughtWorksRadarScraper", "scrape_fuzz_testing"]
