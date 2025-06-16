### Environment setup

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

### Provision environments for Watsonx.data , Orchestrate(For Assistance),Watsonx.ai

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


------------------------------------------------------------------------------------------------------------------------------------------

### Maximo deployment 


### 1. Build the python code as docker image.
```
docker build --platform linux/amd64 -t md8911/maximo-jobplan:latest .
```

### 2. Verify the docker image.
```
docker images
```

### 3. Login to docker image registry and push the image.
```
docker push <<username>>/maximo-jobplan:latest
```

### 4. Login to Openshift and create new Namespace (e.g. maximo-flask)

### 5. Create Secret in maximo-flask namespace
```
oc create secret generic maximo-env-secret \        
  --from-env-file=.env \
  --namespace=maximo-flask
```

### 6. Apply the deployment.yaml
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: maximo-jobplan
  namespace: maximo-flask
spec:
  replicas: 1
  selector:
    matchLabels:
      app: maximo-jobplan
  template:
    metadata:
      labels:
        app: maximo-jobplan
    spec:
      containers:
        - name: maximo-jobplan
          image: <<user_name>>/maximo-jobplan:latest
          ports:
            - containerPort: 5000
          envFrom:
            - secretRef:
                name: maximo-env-secret  # Reference to your secret

```

### 6. Create Service
```
apiVersion: v1
kind: Service
metadata:
  name: maximo-jobplan-service
  namespace: maximo-flask
spec:
  selector:
    app: maximo-jobplan
  ports:
    - protocol: TCP
      port: 80
      targetPort: 5000
  type: ClusterIP
```

### 6. In Networking -> Routes, create Route from service (maximo-jobplan-service) and select Target port (80->5000TCP)

