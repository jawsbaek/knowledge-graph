"""ThoughtWorks Technology Radar web scraper."""

import re
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from loguru import logger

from ...models.radar import (
    RadarEdition,
    RadarItem,
    RadarMovement, 
    RadarQuadrant,
    RadarRing,
    RadarTechnique,
)


class ThoughtWorksRadarScraper:
    """Scraper for ThoughtWorks Technology Radar website."""
    
    def __init__(self, base_url: str = "https://www.thoughtworks.com/radar"):
        """Initialize scraper with base URL.
        
        Args:
            base_url: Base URL for Technology Radar
        """
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
        )
    
    def get_latest_edition_info(self) -> Optional[Dict]:
        """Get information about the latest radar edition.
        
        Returns:
            Dictionary with edition metadata
        """
        try:
            response = self.client.get(self.base_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract volume and date from the main page
            volume_element = soup.find(text=re.compile(r"Volume \d+"))
            if volume_element:
                volume_match = re.search(r"Volume (\d+)", volume_element)
                volume = int(volume_match.group(1)) if volume_match else None
            else:
                volume = None
            
            # Look for date information
            date_element = soup.find(text=re.compile(r"\w+ \d{4}"))
            if date_element:
                date_match = re.search(r"(\w+ \d{4})", date_element)
                edition_date = date_match.group(1) if date_match else None
            else:
                edition_date = None
            
            return {
                "volume": volume,
                "edition_date": edition_date,
                "url": self.base_url
            }
            
        except Exception as e:
            logger.error(f"Failed to get edition info: {e}")
            return None
    
    def scrape_technique(self, technique_path: str) -> Optional[RadarTechnique]:
        """Scrape a specific technique from Technology Radar.
        
        Args:
            technique_path: Path to technique page (e.g., "/techniques/summary/fuzz-testing")
            
        Returns:
            RadarTechnique object or None if failed
        """
        try:
            url = urljoin(self.base_url, technique_path)
            response = self.client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract technique name from URL or page
            name = self._extract_technique_name(technique_path, soup)
            if not name:
                logger.warning(f"Could not extract technique name from {url}")
                return None
            
            # Extract description
            description = self._extract_description(soup)
            
            # Extract ring/adoption level
            ring = self._extract_ring(soup)
            
            # Extract related blips
            related_blips = self._extract_related_blips(soup)
            
            # Get edition info
            edition_info = self.get_latest_edition_info()
            
            return RadarTechnique(
                name=name,
                quadrant=RadarQuadrant.TECHNIQUES,
                ring=ring or RadarRing.ASSESS,  # Default if not found
                movement=RadarMovement.NO_CHANGE,  # Default
                description=description or f"Technology Radar technique: {name}",
                volume=edition_info.get("volume", 32) if edition_info else 32,
                edition_date=edition_info.get("edition_date", "2025-04") if edition_info else "2025-04",
                source_url=url,
                related_blips=related_blips,
                methodology_connections=[],
                practice_connections=[]
            )
            
        except Exception as e:
            logger.error(f"Failed to scrape technique {technique_path}: {e}")
            return None
    
    def scrape_techniques_list(self) -> List[str]:
        """Scrape list of all available techniques.
        
        Returns:
            List of technique paths
        """
        try:
            url = f"{self.base_url}/techniques"
            response = self.client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find links to individual techniques
            technique_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/techniques/summary/' in href:
                    technique_links.append(href)
            
            return list(set(technique_links))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Failed to scrape techniques list: {e}")
            return []
    
    def _extract_technique_name(self, path: str, soup: BeautifulSoup) -> Optional[str]:
        """Extract technique name from path or page content."""
        # Try to get from path first
        path_parts = path.split('/')
        if path_parts and path_parts[-1]:
            # Convert slug to title case
            name = path_parts[-1].replace('-', ' ').title()
            return name
        
        # Try to get from page title or h1
        title_element = soup.find('h1') or soup.find('title')
        if title_element:
            return title_element.get_text().strip()
        
        return None
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract technique description from page content."""
        # Look for description in various places
        
        # Try main content paragraphs
        content_div = soup.find('div', class_=re.compile(r'content|main|description'))
        if content_div:
            paragraphs = content_div.find_all('p')
            if paragraphs:
                return ' '.join(p.get_text().strip() for p in paragraphs[:2])
        
        # Try any paragraph with substantial text
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text().strip()
            if len(text) > 100:  # Substantial description
                return text
        
        return None
    
    def _extract_ring(self, soup: BeautifulSoup) -> Optional[RadarRing]:
        """Extract ring/adoption level from page content."""
        text = soup.get_text().lower()
        
        # Look for ring indicators in the text
        if 'adopt' in text and ('we feel strongly' in text or 'should be adopting' in text):
            return RadarRing.ADOPT
        elif 'trial' in text and ('worth pursuing' in text or 'try this technology' in text):
            return RadarRing.TRIAL
        elif 'assess' in text and ('promising' in text or 'worth exploring' in text):
            return RadarRing.ASSESS
        elif 'hold' in text and ('proceed with caution' in text or 'serious problems' in text):
            return RadarRing.HOLD
        
        return None
    
    def _extract_related_blips(self, soup: BeautifulSoup) -> List[str]:
        """Extract related blips from page content."""
        related_blips = []
        
        # Look for "Related blips" section
        related_section = soup.find(text=re.compile(r'Related blips'))
        if related_section:
            parent = related_section.parent
            if parent:
                # Find links in the related section
                for link in parent.find_all('a'):
                    link_text = link.get_text().strip()
                    if link_text and len(link_text) > 3:
                        related_blips.append(link_text)
        
        return related_blips
    
    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()


# Example usage function
def scrape_fuzz_testing() -> Optional[RadarTechnique]:
    """Scrape the Fuzz Testing technique as an example.
    
    Returns:
        RadarTechnique for Fuzz Testing
    """
    scraper = ThoughtWorksRadarScraper()
    try:
        return scraper.scrape_technique("/techniques/summary/fuzz-testing")
    finally:
        scraper.close()
