import leaders_scraper
leaders = leaders_scraper.get_leaders()
leaders_scraper.save(leaders)