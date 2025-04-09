## Accessing AWS Lambda Functions via the AWS Console

To access AWS Lambda functions, follow the steps below:

1. Go to the following link:  
   [AWS Start Portal](https://d-9c67018f89.awsapps.com/start/#/?tab=accounts)  
   This will take you to the AWS Start Portal, where you can view the AWS accounts you have been granted access to.

2. Look for the following AWS accounts in the list:
   - **NHS Digital DDC Exeter Texas Mgmt**
   - **NHS Digital DDC Exeter Texas NonProd K8s**
   - **NHS Digital DDC Exeter Texas Prod K8s**


   *If you do not see these accounts listed, please contact the Texas Platform team for access.*

   ![AWS Account List](docs/images/aws-accounts.png)

3. When working in development, you should use the **NHS Digital DDC Exeter Texas NonProd K8s** account and log in as the **bcss-rw-user**.

4. Once your AWS Console has loaded, **change the region to `eu-west-2` (London)** using the region selector in the top-right corner of the Console.

   ![Changing the region](docs/images/region-change.png)

5. Once your AWS Console has loaded, use the search bar in the upper-left corner and search for **Lambda**.

   ![Searching for Lambda](docs/images/lambda-search.png)

6. On the main Lambda service page, select **Functions** from the sidebar.

   ![Lambda Functions List](docs/images/lambda-functions-list.png)

7. You should now see a page listing all available Lambda functions.  
   **Be careful not to modify any functions unless you are certain they are managed by this team,** as some functions are managed by other teams.

8. Use the search bar on this page to find the specific Lambda function you are working on.  
   Currently, our Lambda functions are named:

   - bcss-s3-to-lambda-trigger
   - bcss_notify_callback
   - bcss-lambda-s3-oracle