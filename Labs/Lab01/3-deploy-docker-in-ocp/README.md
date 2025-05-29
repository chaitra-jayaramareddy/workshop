
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

