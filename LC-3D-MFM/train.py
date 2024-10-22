from utils import *
from model import *
from loss_function import *
from image_formation import *

if __name__ == "__main__":
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Resize((240, 240)),
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
    ])
    train_data = [torch.randn(3, 240, 240) for _ in range(100)]
    # train_dataset = FaceDataset(train_data, transform=transform)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    model = FullFaceModel()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    rotate_function = ProjectFunction()
    land_mark_loss = LandMarkLoss()


    # Training Loop - Stage 1: Pose Pretraining
    for epoch in range(num_epochs // 3):
        model.train()
        running_loss = 0.0

        for frames in train_loader:
            _, _, geometry_graph, _, poses = model(frames)

            output = rotate_function(geometry_graph, poses)
            loss = land_mark_loss(output, geometry_graph)

            # Backward and optimize
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        # Print epoch loss
        print(f"Pose Pretraining Epoch [{epoch + 1}/{num_epochs // 3}], Loss: {running_loss / len(train_loader):.4f}")

    # Training Loop - Stage 2: Identity Pretraining
    for epoch in range(num_epochs // 3):
        model.train()
        running_loss = 0.0

        for frames in train_loader:
            # Forward pass
            identities, _, _, _, _ = model.siamese_model(frames)

            # Giả lập loss cho huấn luyện danh tính
            loss = criterion(identities[0], torch.randn_like(identities[0]))
            loss += criterion(reflectances[0], torch.randn_like(reflectances[0]))

            # Backward and optimize
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        # Print epoch loss
        print(
            f"Identity Pretraining Epoch [{epoch + 1}/{num_epochs // 3}], Loss: {running_loss / len(train_loader):.4f}")

    # Training Loop - Stage 3: Combined Training
    for epoch in range(num_epochs // 3, num_epochs):
        model.train()
        running_loss = 0.0

        for frames in train_loader:
            # Forward pass
            face_geometry, reflectance_output, geometry_graph, illuminations, poses = model(frames)

            # Giả lập loss cho huấn luyện kết hợp
            loss = criterion(face_geometry, torch.randn_like(face_geometry))
            loss += criterion(reflectance_output, torch.randn_like(reflectance_output))

            # Backward and optimize
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        # Print epoch loss
        print(f"Combined Training Epoch [{epoch + 1}/{num_epochs}], Loss: {running_loss / len(train_loader):.4f}")

    print("Training completed.")