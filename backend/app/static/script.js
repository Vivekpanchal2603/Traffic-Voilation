function previewVideo(event) {
    const video = document.getElementById("videoPreview");

    video.src = URL.createObjectURL(event.target.files[0]);
    video.style.display = "block";
}


async function uploadVideo() {
    const fileInput = document.getElementById("videoFile");
    const status = document.getElementById("status");
    const resultDiv = document.getElementById("result");

    if (!fileInput.files.length) {
        alert("Please select a video.");
        return;
    }

    status.innerHTML = "📤 Uploading video...";
    resultDiv.innerHTML = `
        <div class="result-item">
            <span>Status:</span>
            <strong>Processing...</strong>
        </div>
    `;

    clearPreviewImages();

    try {
        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        // Upload
        const uploadRes = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const uploadData = await uploadRes.json();

        status.innerHTML = "🧠 Running AI Detection Pipeline...";

        // Process
        const processRes = await fetch(`/process/${uploadData.job_id}`, {
            method: "POST"
        });

        const processData = await processRes.json();
        const result = processData.result;

        status.innerHTML = "✅ Processing Complete";

        resultDiv.innerHTML = `
            <div class="result-item">
                <span>Violation Detected</span>
                <strong>${result.violation_detected ? "YES" : "NO"}</strong>
            </div>

            <div class="result-item">
                <span>No Helmet</span>
                <strong>${result.no_helmet ?? "--"}</strong>
            </div>

            <div class="result-item">
                <span>Triple Seat</span>
                <strong>${result.triple_seat ?? "--"}</strong>
            </div>

            <div class="result-item">
                <span>Plate Number</span>
                <strong>${result.plate_number || "Pending"}</strong>
            </div>

            <div class="result-item">
                <span>Saved Plate Crops</span>
                <strong>${result.plates_saved}</strong>
            </div>
        `;

        renderPreviewImages(uploadData.job_id);

    } catch (error) {
        console.error(error);

        status.innerHTML = "❌ Processing Failed";

        resultDiv.innerHTML = `
            <div class="result-item">
                <span>Error</span>
                <strong>Could not process video.</strong>
            </div>
        `;
    }
}


/* ---------- PREVIEW IMAGE RENDERING ---------- */

function renderPreviewImages(jobId) {
    const platePreview = document.getElementById("platePreview");
    const framePreview = document.getElementById("framePreview");

    platePreview.innerHTML = "";
    framePreview.innerHTML = "";

    // Show only top 3 plate images
    for (let i = 1; i <= 3; i++) {
        const img = createPreviewImage(
            `/outputs/${jobId}/plates/plate_best_${i}.jpg`
        );
        platePreview.appendChild(img);
    }

    // Show only top 3 violation frames
    for (let i = 1; i <= 3; i++) {
        const img = createPreviewImage(
            `/outputs/${jobId}/full_frames/frame_best_${i}.jpg`
        );
        framePreview.appendChild(img);
    }
}


function createPreviewImage(src) {
    const img = document.createElement("img");

    img.src = src;

    img.onerror = () => img.remove();

    img.onclick = () => openImageModal(src);

    return img;
}


function openImageModal(src) {
    let modal = document.getElementById("imageModal");

    if (!modal) {
        modal = document.createElement("div");
        modal.id = "imageModal";
        modal.className = "image-modal";

        modal.innerHTML = `
            <span class="close-modal">&times;</span>
            <img id="modalImage" class="modal-image">
        `;

        document.body.appendChild(modal);

        modal.onclick = () => {
            modal.style.display = "none";
        };
    }

    document.getElementById("modalImage").src = src;
    modal.style.display = "flex";
}


function clearPreviewImages() {
    document.getElementById("platePreview").innerHTML = "";
    document.getElementById("framePreview").innerHTML = "";
}