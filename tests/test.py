import cv2
from insightface.app import FaceAnalysis
from PIL import Image

providers = ["CPUExecutionProvider"]
provider_options = [{"arena_extend_strategy": "kSameAsRequested"}] * len(providers)

app = FaceAnalysis(
    name="buffalo_l",
    root="./insightface",
    providers=providers,
    provider_options=provider_options,
)
app.prepare(ctx_id=0, det_size=(640, 640))

img = cv2.imread("/mnt/onedrive/picnik-data/2023/12/test.jpg")
faces = app.get(img)

# print(faces)

for face in faces:
    print(len(face["embedding"]))
    bbox = [int(point) for point in face["bbox"]]
    [x1, y1, x2, y2] = bbox
    print(img.shape)
    print([x1, y1, x2, y2])
    print([x1 - 50, y1 - 50, x2 + 50, y2 + 50])

    height = y2 - y1
    width = x2 - x1

    area = height * width
    img_area = img.shape[0] * img.shape[1]
    print([height, width])
    print(area)
    print(img_area)
    print((area / img_area) * 100)

    img = cv2.rectangle(img, (x1 - 8, y1), (x2 + 8, y2), color=(0, 255, 0))

cv2.imwrite("./t1_output.jpg", img)
# display(Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)))
