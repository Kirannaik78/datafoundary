# Email processor

## Description
Project to process email based on the rules defined in the rules.json file and update database with respective action


# SetUp
1. clone the repository
2. Install Dependencies by running below code
   ``` pip2 install -r requirement.txt ```
3. Setup Database 
   ```mysql> source all_db.sql ```
4. Set up a service account and download the JSON key file from the Google Cloud Console.
5. create and replace credentials.json 
6. remove token.json file if your running for the first time
7. Run the fetch script
   ``` python3 fetch_emails.py```
8. Place your rules in `rules.json`
9. Run the processing script
   ```python3 process_emails.py```

# Notes:

I have mentioned comment for each line of code so that it will be helpfully while reading

 ## Problems
* Program could be optimized to fetch the mails in batch which would have improved processing time
* Program is updating actions in the database like update is_read column and folder column instead of taking actually action
