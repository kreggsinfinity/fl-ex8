import sys
import asyncio
from business_generator import run_business_generation

def main():
    print("Starting Business English Pro generator (9:16 Vertical Reel)...")
    video_p, meta = asyncio.run(run_business_generation(idx=0))
    print(f"Done! Final video generated: {video_p}")

if __name__ == "__main__":
    main()
