# APIs for Musicmoney Image gen agent, based on the work by Create Protocol AI infra

# Rishi API

This API provides a flexible and extensible platform for various media processing tasks. Currently, it supports image processing operations, including model training and inference, with plans to expand to other media types in the future.
createprotocol.org
## Features

- Image processing
  - Dreambooth model training
  - Image generation using trained models
- Modular architecture for easy expansion to other media types
- Support for multiple backend providers (currently Salad and Replicate)
- File storage using Cloudflare R2 for both input and output files
- Asynchronous job processing with webhook notifications
- Comprehensive API documentation using Swagger and ReDoc

## Getting Started

### Prerequisites

- Python 3.7+
- Redis server
- Salad API key (for Salad provider)
- Replicate API token (for Replicate provider)
- Cloudflare R2 account and credentials

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/createprotocol/rishi-api.git
   cd media-processing-api
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the project root and add the following:
   ```
   SALAD_API_KEY=your_salad_api_key
   SALAD_ORG_NAME=your_salad_org_name
   REPLICATE_API_TOKEN=your_replicate_api_token
   R2_ACCESS_KEY_ID=your_r2_access_key_id
   R2_SECRET_ACCESS_KEY=your_r2_secret_access_key
   R2_ENDPOINT=https://your-account-id.r2.cloudflarestorage.com
   R2_BUCKET_NAME=your_r2_bucket_name
   ```

5. Start the Redis server:
   ```
   docker run -d -p 6379:6379 redis
   ```

6. Run the application:
   ```
   python app.py
   ```

The API will be available at `http://localhost:5000`.

## API Documentation

- Swagger UI: `http://localhost:5000/swagger-ui`
- ReDoc: `http://localhost:5000/redoc`

These interactive documentation interfaces provide detailed information about each endpoint, including request/response schemas and example usage.

## Usage Examples

### Image Processing

1. Upload images and start a Dreambooth training job:
   ```bash
   curl -X POST -F "files=@image1.jpg" -F "files=@image2.jpg" \
        -F "instance_prompt=photo of TOK dog" \
        -F "webhook_url=https://your-webhook-url.com" \
        -F "provider=salad" \
        http://localhost:5000/image/upload
   ```

2. Run inference using a trained model:
   ```bash
   curl -X POST http://localhost:5000/image/inference \
   -H "Content-Type: application/json" \
   -d '{
     "Lora_url": "https://your-r2-bucket.com/trained_model.tar",
     "prompt": "a photo of TOK dog in a park",
     "num_outputs": 1,
     "webhook_url": "https://your-webhook-url.com"
   }'
   ```

3. Webhook Response:
   When a job is completed, the webhook will receive a response with R2 URLs for the results:
   - For inference jobs: A list of R2 URLs for the generated images
   - For training jobs: An R2 URL for the trained model file

## File Storage

All input files (images for training) and output files (generated images and trained models) are stored in Cloudflare R2. The API returns pre-signed URLs for accessing these files, which expire after a set time (default is 1 hour).

## Extending the API

The API is designed with modularity in mind, making it easy to add support for new media types or processing tasks:

1. Create a new blueprint for the media type (e.g., `audio_blueprint.py`).
2. Define the necessary routes and logic within the blueprint.
3. Create corresponding schemas in `schemas.py`.
4. Register the new blueprint in `app.py`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
