Algorithm Documentation: Cosine Similarity
===========================================

This document provides an overview of the Cosine Similarity algorithm used for user recommendation and job recommendation in the LinkedOut project.

Overview
--------
Cosine similarity is a metric used to measure how similar two vectors are irrespective of their magnitude. In the context of recommendation systems, it's often used to measure the similarity between user profiles or job descriptions.

Steps Involved
--------

1. **Input**: 
   - User skills in the form of a vector.
   - Each vector contains the values of all 18 skills rated from 0 to 5.

2. **Process**:
   - Calculate the cosine angle between two vectors.
   - We calculate this similarity between either two user vectors or a user vector and a job vector.
   - The cosine similarity value ranges from -1 to 1:
     - 1 indicates that the vectors are identical.
     - 0 indicates that the vectors are orthogonal (no similarity).
     - -1 indicates that the vectors are completely opposite.
   - Higher cosine similarity value implies that the users or job recommendations are more similar.

3. **Usage in LinkedOut**:
   - **User Recommendation**: Used to find users with similar profiles based on skills.
   - **Job Recommendation**: Used to recommend jobs based on job descriptions that are similar in skills and requirements.
