# Setup Instructions

- Prepare Python environment
  ```sh
  python3.10 -m venv .venv
  source .venv/bin/activate
  pip install arcgis \ 
              arcgis-mapping \
              colorama \
              rasterio \
              pyproj \
              tqdm \
              keyring.alt
  ```

- Configure keyring
    ```sh
    # File $HOME/.config/python_keyring/keyringrc.cfg
    [backend]
    default-keyring=keyrings.alt.file.PlaintextKeyring
    ```