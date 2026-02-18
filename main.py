import traceback
from scraper import KufarScraper

def main():
    """Main entry point"""
    try:
        token = input("Enter your authorization token: ").strip()
        if not token:
            print("Token cannot be empty")
            return
        
        scraper = KufarScraper(token)
        scraper.scrape()
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()