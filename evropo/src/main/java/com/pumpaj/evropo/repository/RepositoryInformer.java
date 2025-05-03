package com.pumpaj.evropo.repository;

import com.pumpaj.evropo.model.ModelInformer;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

@Repository
public interface RepositoryInformer extends MongoRepository<ModelInformer, String> {

    // Find by URL
    Optional<ModelInformer> findByUrl(String url);

    // Find all unvisited articles
    List<ModelInformer> findByVisitedFalse();

    // Find by title containing specific words (case-insensitive)
    List<ModelInformer> findByTitleContainingIgnoreCase(String keyword);

    // Check if article exists by URL
    boolean existsByUrl(String url);

    // Find by visited status
    List<ModelInformer> findByVisited(boolean visited);
}