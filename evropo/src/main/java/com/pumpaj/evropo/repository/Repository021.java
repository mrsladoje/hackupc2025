package com.pumpaj.evropo.repository;

import com.pumpaj.evropo.model.Model021;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

@Repository
public interface Repository021 extends MongoRepository<Model021, String> {

    // Find by URL
    Optional<Model021> findByUrl(String url);

    // Find all unvisited articles
    List<Model021> findByVisitedFalse();

    // Find by title containing specific words (case-insensitive)
    List<Model021> findByTitleContainingIgnoreCase(String keyword);

    // Check if article exists by URL
    boolean existsByUrl(String url);

    // Find by visited status
    List<Model021> findByVisited(boolean visited);
}