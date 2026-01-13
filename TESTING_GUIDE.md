# Testing Guide: RAG Functionality on Render

## ✅ Implementation Complete

The persistent vector store has been implemented with the following features:

1. **Persistent Storage**: Vector embeddings are saved to `vectorstore_data/vectorstore.pkl`
2. **Auto-reload on Startup**: Documents are automatically reloaded from the database when the server starts
3. **Auto-save on Upload**: New documents are automatically saved to disk when uploaded
4. **Multi-worker Support**: Each worker can auto-reload missing documents from the database

## 🧪 Testing Steps After Deployment

### Step 1: Deploy to Render

1. Commit and push your changes:
   ```bash
   git add .
   git commit -m "Add persistent vector store for RAG functionality"
   git push origin main
   ```

2. Wait for Render to build and deploy your application

### Step 2: Check Deployment Logs

After deployment, check the Render logs for these messages:

✅ **Expected Success Messages:**
```
✅ Vector store initialized on startup
🔄 Reloading documents into vector store...
📄 Found X documents with extracted text
✅ Reloaded: filename.pdf (X chunks)
✅ Successfully reloaded X/X documents (X total chunks)
💾 Saved X chunks to /app/vectorstore_data/vectorstore.pkl
```

⚠️ **If you see warnings:**
- `⚠️ Warning: Document reload failed` - This is OK if you have no documents yet
- `📂 No existing vector store found` - This is normal on first deployment

### Step 3: Test Document Upload

1. **Login to your deployed application**
2. **Upload a test document** (PDF, DOCX, or TXT)
3. **Check the logs** - You should see:
   ```
   ✅ Ingested X chunks for document Y
   💾 Saved X chunks to /app/vectorstore_data/vectorstore.pkl
   ```

### Step 4: Test RAG Functionality

1. **Ask a question about the uploaded document:**
   - Example: "explain this document" or "what is this document about?"
   
2. **Expected Behavior:**
   - The bot should respond with information **specific to your document**
   - The response should reference content from your uploaded document
   - NOT just generic answers

3. **Test Multiple Documents:**
   - Upload a second document
   - Ask questions like "explain the first document" or "explain the second document"
   - The bot should distinguish between documents

### Step 5: Test After Restart

1. **Restart your Render service** (or wait for an auto-restart)
2. **Check logs** - Documents should be automatically reloaded
3. **Ask the same question** - Should still work without re-uploading

## 🔍 Debugging Tips

### If RAG is NOT working:

1. **Check Render Logs:**
   - Look for error messages about SentenceTransformer
   - Check if documents are being reloaded
   - Verify the model is loading

2. **Verify Document Extraction:**
   - Check if `extracted_text` is saved in the database
   - You can verify this in Django admin or by checking the Document model

3. **Check Vector Store:**
   - Look for messages like "Loaded X chunks from..."
   - If you see "No existing vector store found", documents need to be uploaded

4. **Test Locally First:**
   ```bash
   python manage.py reload_documents
   ```
   This should show you if documents are being loaded correctly

### Common Issues:

**Issue: "Model is not loaded"**
- **Solution**: Check if `sentence-transformers` is in requirements.txt
- Verify the model downloads correctly (check logs)

**Issue: "No chunks found"**
- **Solution**: Documents might not have `extracted_text` saved
- Re-upload the documents

**Issue: "Generic answers only"**
- **Solution**: 
  - Check if `document_text` is being retrieved (check logs)
  - Verify documents are in the vector store
  - Check if `retrieve_context` is returning results

## 📊 Verification Checklist

After deployment, verify:

- [ ] Server starts without errors
- [ ] Vector store initializes successfully
- [ ] Documents can be uploaded
- [ ] Upload shows "Ingested X chunks" message
- [ ] Questions about documents return document-specific answers
- [ ] After restart, documents are automatically reloaded
- [ ] Multiple documents work correctly

## 🚀 Expected Behavior

**Before Fix:**
- ❌ Generic answers only
- ❌ No document context in responses
- ❌ RAG not working after deployment

**After Fix:**
- ✅ Document-specific answers
- ✅ Context from uploaded documents
- ✅ Works after restarts
- ✅ Persists across deployments

## 📝 Notes

- The vector store file is saved in `vectorstore_data/` directory
- Each worker process has its own vector store instance
- Documents are auto-reloaded if missing from a worker's memory
- The database stores `extracted_text` as a backup

## 🆘 Still Having Issues?

If RAG is still not working after following these steps:

1. Share the Render logs (especially startup and document upload logs)
2. Verify your `GROQ_API_KEY` is set in Render environment variables
3. Check that `sentence-transformers` is installed (should be in requirements.txt)
4. Test the `reload_documents` command manually in Render shell
