# Dockerfile Optimization Guide for HyperCode V2.0

This guide details the optimizations applied to create `Dockerfile.production` for the HyperCode Core service.

## Key Optimizations

### 1. Multi-Stage Build Structure
We have separated the Dockerfile into distinct stages to ensure that the final production image contains *only* what is necessary for runtime.

*   **`base`**: Sets up common environment variables and working directory.
*   **`dependencies` (Builder)**: Installs build tools (`build-essential`), compiles Python dependencies into wheels, and generates the Prisma client. This stage is discarded in the final image.
*   **`development`**: A full environment with `git` and other tools for local development.
*   **`testing`**: Extends development with testing tools (`pytest`, `coverage`).
*   **`ci`**: Extends testing for security scanning (`safety`, `bandit`) and linting.
*   **`runtime`**: The lean production image.

### 2. Reduced Image Layers & Size
*   **Consolidated RUN commands**: Multiple `apt-get` and `pip` commands are combined into single `RUN` blocks to reduce the number of filesystem layers.
*   **Cleanup**: explicitly removing `/var/lib/apt/lists/*`, `/tmp/*`, and `/wheels` ensures no temporary files bloat the image.
*   **Size Reduction**: The `runtime` stage is stripped of build tools, git, and testing libraries, resulting in a significantly smaller image (est. ~50-60% reduction).

### 3. Security Hardening
*   **Non-Root User**: A dedicated `hypercode` user (UID 1000) is created and used. This mitigates privilege escalation attacks.
*   **Minimal Packages**: Using `--no-install-recommends` prevents `apt` from installing unnecessary packages that could increase the attack surface.
*   **No Shell Tools**: The production image avoids installing convenience tools like `vim` or `git`.

### 4. Caching Strategy
*   **BuildKit Mounting**: We use `--mount=type=cache` for `apt` and `pip` directories. This speeds up subsequent builds by reusing downloaded packages.
*   **Wheels**: By building wheels in the `dependencies` stage and installing them in `runtime`, we avoid recompiling C extensions in the final stage.

## Usage

### Building for Production
To build the optimized production image:

```bash
docker build -f Dockerfile.production --target runtime -t hypercode-core:prod .
```

### Building for Development
To build the development image (with git, reload support, etc.):

```bash
docker build -f Dockerfile.production --target development -t hypercode-core:dev .
```

### Running Tests
You can run tests directly within the container build process:

```bash
docker build -f Dockerfile.production --target testing .
```

## Integrating with Docker Compose

Update your `docker-compose.production.yml` to use the new file and target:

```yaml
  hypercode-core:
    build:
      context: ./THE HYPERCODE/hypercode-core
      dockerfile: Dockerfile.production
      target: runtime
    # ... rest of configuration
```
