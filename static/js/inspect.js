import { pdfjs } from 'https://cdn.jsdelivr.net/npm/ @react-pdf-viewer/core@3.3.1/lib/es/index.js';
pdfjs.GlobalWorkerOptions.workerSrc = '//cdn.jsdelivr.net/npm/pdfjs-dist@4.5.136/legacy/build/pdf.worker.min.js';

const canvas = document.querySelector('canvas');
const ctx = canvas.getContext('2d');

let pdfDoc = null;

async function loadPage(pageNum = 1) {
  if (!pdfDoc) {
    const loadingTask = pdfjs.getDocument({ url: '/sample-statements/sample-bank-statement.pdf' });
    pdfDoc = await loadingTask.promise.promise;
  }

  const page = await pdfDoc.getPage(pageNum);
  const viewport = page.getViewport({ scale: 1.5 });
  canvas.height = viewport.height;
  canvas.width = viewport.width;

  await page.render({ canvasContext: ctx, viewport }).promise;
}

document.getElementById('zoom-in').addEventListener('click', () => {
  alert("Zoom In functionality needs backend integration.");
});

document.getElementById('zoom-out').addEventListener('click', () => {
  alert("Zoom Out functionality needs backend integration.");
});

document.getElementById('create-table').addEventListener('click', () => {
  alert("Draw rectangle to define region.");
});

document.getElementById('add-column').addEventListener('click', () => {
  alert("Click to place column.");
});

document.getElementById('add-row').addEventListener('click', () => {
  alert("Click to place row.");
});

document.getElementById('extract-grids').addEventListener('click', () => {
  alert("Extracting grids...");
});

loadPage();
