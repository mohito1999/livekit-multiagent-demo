def save_transcript(agent, job_id):
    os.makedirs("transcripts", exist_ok=True)
    file_path = f"transcripts/{job_id}.txt"
    
    with open(file_path, "w") as f:
        f.write(f"Transcript for Job: {job_id}\n")
        f.write("="*40 + "\n\n")
        for msg in agent.chat_ctx.items:
            role = msg.role.upper()
            if role == "SYSTEM":
                continue
            content = msg.content
            if isinstance(content, list):
                content = " ".join([str(c) for c in content])
            f.write(f"[{role}]: {content}\n\n")
            
    logger.info(f"Transcript saved to {file_path}")
