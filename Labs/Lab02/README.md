### Environment stepup

### 1. Setup account in Image registry (For example : https://hub.docker.com)

### 2. Create a `.env` File or use the file provided in src folder
Create a `.env` file
```
MAXIMO_URL=https://<<YOUR_MAXIMO_INSTANCE>>/maximo/api/os/mxapijobplan?lean=1
API_KEY=YOUR_MAXIMO_API_KEY
```

### 3. Generate API Key
To generate a WatsonX API key, follow the instructions in the official IBM documentation:
[Create WatsonX API Key](https://www.ibm.com/docs/en/masv-and-l/maximo-manage/continuous-delivery?topic=setup-create-watsonx-api-key)

--------------------------------------------------------------------------------------------------------------------------------------
### Provision environements for watsonx data , orchestrate(for assistance),watsonx.ai

TechZone Certified Base Images 

https://techzone.ibm.com/collection/tech-zone-certified-base-images/journey-watsonx

Watonsx.data : https://techzone.ibm.com/my/reservations/create/67e6c2a9bc768d343f1c08ea

Watsonx.Orchestrate/AI : https://techzone.ibm.com/my/reservations/create/67d2f22a74a8be45b4f52bc5

How to reserve : https://www.ibm.com/support/pages/how-create-reservation-techzone


### 1. Create a temporary file(notepad/texteditor) in your local machine to save key information such as,

Watson data Information
1.			Milvus service GRPC host - 
2.			Milvus service GRPC port
3.			Milvus host URL : https://<grpc hostname>:<grpc port>


Watsonx Information
1.			URL (https://dataplatform.cloud.ibm.com)
2.			Project ID 
3.			API Key (IAM) 
