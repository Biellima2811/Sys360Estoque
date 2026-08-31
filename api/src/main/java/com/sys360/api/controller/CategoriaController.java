package com.sys360.api.controller;

import com.sys360.api.modelo.Categoria;
import com.sys360.api.repository.CategoriaRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/categorias")
public class CategoriaController {
    // O Spring injeta o repositorio automaticamente aqui
    @Autowired
    private CategoriaRepository repository;

    // Rota para criar um categoria;
    @PostMapping
    public Categoria cadastrar(@RequestBody Categoria categoria){
        return repository.save(categoria);
    }
    // Rota para listar todas as categorias

    @GetMapping
    public List<Categoria> listar() {
        return repository.findAll();
    }
}
