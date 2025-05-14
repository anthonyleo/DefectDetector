import cv2

def main():
    cv2.namedWindow("Key Test")

    print("Press any key to see its number. Press ESC to exit.")

    while True:
        key = cv2.waitKey(0) & 0xFF
        print(f"Key pressed: {key}")

        if key == 27:  # ESC key
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()