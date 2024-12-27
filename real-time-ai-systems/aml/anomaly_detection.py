import tensorflow as tf

class GanEncAnomalyDetector(tf.keras.Model):
    
    def __init__(self, input_dim):
        super(GanEncAnomalyDetector, self).__init__()
        
        self.input_dim = input_dim
        self.latent_dim = [1, input_dim[1]] 
        self.d_steps = 3
        self.gp_weight = 10 
        
        self.encoder = self.make_encoder_model(self.input_dim)
        self.generator = self.make_generator(self.input_dim, self.latent_dim)
        self.discriminator = self.make_discriminator_model(self.input_dim)

        self.mse = tf.keras.losses.MeanSquaredError()
        
        self.epoch_e_loss_avg = tf.keras.metrics.Mean(name="epoch_e_loss_avg")
        self.epoch_d_loss_avg = tf.keras.metrics.Mean(name="epoch_d_loss_avg")
        self.epoch_g_loss_avg = tf.keras.metrics.Mean(name="epoch_g_loss_avg")
        self.epoch_a_score_avg = tf.keras.metrics.Mean(name="epoch_a_score_avg")

        @property
        def metrics(self):
            return [
                self.epoch_e_loss_avg,
                self.epoch_d_loss_avg,
                self.epoch_g_loss_avg,
                self.epoch_a_score_avg,
            ]

    # define model architectures
    def make_encoder_model(self, input_dim):
        inputs = tf.keras.layers.Input(shape=(input_dim[0],input_dim[1]))
        x = tf.keras.layers.Conv1D(filters = 64, kernel_size= 1,padding='same', kernel_initializer="uniform")(inputs)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.LeakyReLU(alpha=0.2)(x)    
        x = tf.keras.layers.MaxPooling1D(pool_size=2, padding='same')(x)
        x = tf.keras.layers.Conv1D(filters = input_dim[1], kernel_size= 1,padding='same',  kernel_initializer="uniform")(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.LeakyReLU(alpha=0.2)(x)    
        x = tf.keras.layers.MaxPooling1D(pool_size=2, padding='same')(x)    
        encoder = tf.keras.Model(inputs=inputs, outputs=x, name="encoder_model")
        return encoder

    def make_generator(self, input_dim, latent_dim):
        latent_inputs = tf.keras.layers.Input(shape=(latent_dim[0],latent_dim[1]))
        x = tf.keras.layers.Conv1D(filters = 8, kernel_size= 1,padding='same', kernel_initializer="uniform")(latent_inputs) 
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.LeakyReLU(alpha=0.2)(x)    
        x = tf.keras.layers.UpSampling1D(2)(x) 
        x = tf.keras.layers.Conv1D(filters = 16, kernel_size= 1,padding='same', kernel_initializer="uniform")(x) 
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.LeakyReLU(alpha=0.2)(x)    
        #x = tf.keras.layers.UpSampling1D(2)(x) 
        x = tf.keras.layers.Conv1D(filters = input_dim[1], kernel_size= 1,padding='same', kernel_initializer="uniform")(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.LeakyReLU(alpha=0.2)(x)    
        generator = tf.keras.Model(inputs=latent_inputs, outputs=x, name="generator_model")        
        return generator

    def make_discriminator_model(self, input_dim):
        inputs = tf.keras.layers.Input(shape=(input_dim[0],input_dim[1]))
        x = tf.keras.layers.Conv1D(filters = 128, kernel_size= 1,padding='same', kernel_initializer="uniform")(inputs)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.LeakyReLU(alpha=0.2)(x)    
        x = tf.keras.layers.MaxPooling1D(pool_size=2, padding='same')(x)
        x = tf.keras.layers.Conv1D(filters = 64, kernel_size= 1,padding='same', kernel_initializer="uniform")(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.LeakyReLU(alpha=0.2)(x)    

        # dense output layer
        x = tf.keras.layers.Flatten()(x)    
        x = tf.keras.layers.LeakyReLU(0.2)(x)
        x = tf.keras.layers.Dense(128)(x)
        x = tf.keras.layers.LeakyReLU(0.2)(x)
        prediction = tf.keras.layers.Dense(1)(x)
        discriminator = tf.keras.Model(inputs=inputs, outputs=prediction, name="discriminator_model" )               
        return discriminator
        
    # Training function
    @tf.function
    def train_step(self, real_data):
        if isinstance(real_data, tuple):
            real_data = real_data[0]

        # Get the batch size
        batch_size = tf.shape(real_data)[0]

        # For each batch, we are going to perform the
        # following steps as laid out in the original paper:
        # 1. Train the generator and get the generator loss
        # 1a. Train the encoder and get the encoder loss
        # 2. Train the discriminator and get the discriminator loss
        # 3. Calculate the gradient penalty
        # 4. Multiply this gradient penalty with a constant weight factor
        # 5. Add the gradient penalty to the discriminator loss
        # 6. Return the generator and discriminator losses as a loss dictionary

        # Train the discriminator first. The original paper recommends training
        # the discriminator for `x` more steps (typically 5) as compared to
        # one step of the generator. Here we will train it for 3 extra steps
        # as compared to 5 to reduce the training time.
        for i in range(self.d_steps):
            # Get the latent vector
            random_latent_vectors = tf.random.normal(shape=(batch_size, self.latent_dim[0], self.latent_dim[1])), 
            with tf.GradientTape() as tape:
                # Generate fake data from the latent vector
                fake_data = self.generator(random_latent_vectors, training=True)

                #(somewhere here step forward?)
                # Get the logits for the fake data
                fake_logits = self.discriminator(fake_data, training=True)
                # Get the logits for the real data
                real_logits = self.discriminator(real_data, training=True)

                # Calculate the discriminator loss using the fake and real sample logits
                d_cost = self.discriminator_loss(real_sample=real_logits, fake_sample=fake_logits)
                # Calculate the gradient penalty
                gp = self.gradient_penalty(real_data, fake_data)
                # Add the gradient penalty to the original discriminator loss
                d_loss = d_cost + gp * self.gp_weight

            # Get the gradients w.r.t the discriminator loss
            d_gradient = tape.gradient(d_loss, self.discriminator.trainable_variables)
            # Update the weights of the discriminator using the discriminator optimizer
            self.d_optimizer.apply_gradients(
                zip(d_gradient, self.discriminator.trainable_variables)
            )

        # Train the generator
        # Get the latent vector
        random_latent_vectors = tf.random.normal(shape=(batch_size, self.latent_dim[0], self.latent_dim[1]))
        with tf.GradientTape() as tape:
            # Generate fake data using the generator
            generated_data = self.generator(random_latent_vectors, training=True)
            # Get the discriminator logits for fake data
            gen_sample_logits = self.discriminator(generated_data, training=True)
            # Calculate the generator loss
            g_loss = self.generator_loss(gen_sample_logits)

        # Get the gradients w.r.t the generator loss
        gen_gradient = tape.gradient(g_loss, self.generator.trainable_variables)
        # Update the weights of the generator using the generator optimizer
        self.g_optimizer.apply_gradients(
            zip(gen_gradient, self.generator.trainable_variables)
        )

        # Train the encoder
        with tf.GradientTape() as tape:
            generated_data = self.generator(random_latent_vectors, training=True)
            # Compress generate fake data from the latent vector
            encoded_fake_data = self.encoder(generated_data, training=True)
            # Reconstruct encoded generate fake data
            generator_reconstructed_encoded_fake_data = self.generator(encoded_fake_data, training=True)
            # Encode the latent vector
            encoded_random_latent_vectors = self.encoder(tf.random.normal(shape=(batch_size, self.input_dim[0], self.input_dim[1])), 
                                                         training=True)
            # Calculate encoder loss
            e_loss = self.encoder_loss(generated_data, generator_reconstructed_encoded_fake_data)

        # Get the gradients w.r.t the generator loss
        enc_gradient = tape.gradient(e_loss, self.encoder.trainable_variables)
        # Update the weights of the generator using the generator optimizer
        self.e_optimizer.apply_gradients(
            zip(enc_gradient, self.encoder.trainable_variables)
        )

        anomaly_score = self.compute_anomaly_score(real_data)

        self.epoch_d_loss_avg.update_state(d_loss)
        self.epoch_g_loss_avg.update_state(g_loss)
        self.epoch_e_loss_avg.update_state(e_loss)
        self.epoch_a_score_avg.update_state(anomaly_score["anomaly_score"])

        return {"d_loss": d_loss, "g_loss": g_loss, "e_loss": e_loss, "anomaly_score": anomaly_score["anomaly_score"]}

    @tf.function
    def test_step(self, input):
        if isinstance(input, tuple):
            input = input[0]
        
        batch_size = tf.shape(input)[0]
        random_latent_vectors = tf.random.normal(shape=(batch_size, self.latent_dim[0], self.latent_dim[1]))
        # Generate fake data using the generator
        generated_data = self.generator(random_latent_vectors, training=False)
        # Get the discriminator logits for fake data
        gen_sample_logits = self.discriminator(generated_data, training=False)
        # Calculate the generator loss
        g_loss = self.generator_loss(gen_sample_logits)

        
        # Compress generate fake data from the latent vector
        encoded_fake_data = self.encoder(generated_data, training=False)
        # Reconstruct encoded generate fake data
        generator_reconstructed_encoded_fake_data = self.generator(encoded_fake_data, training=False)

        # Calculate encoder loss
        e_loss = self.encoder_loss(generated_data, generator_reconstructed_encoded_fake_data)
        
        anomaly_score = self.compute_anomaly_score(input)
        return {
            "g_loss": g_loss,
            "e_loss": e_loss,
            "anomaly_score": anomaly_score["anomaly_score"]
        }
    
    # define custom server function
    @tf.function
    def serve_function(self, input):
        return self.compute_anomaly_score(input)

    def call(self, input):
        if isinstance(input, tuple):
            input = input[0]
        
        encoded = self.encoder(input)
        decoded = self.generator(encoded)
        anomaly_score = self.compute_anomaly_score(input)
        return anomaly_score["anomaly_score"], decoded

    def compile(self):
        super(GanEncAnomalyDetector, self).compile()     
        # Define optimizers
        self.e_optimizer = tf.keras.optimizers.SGD(learning_rate=0.00001, clipnorm=0.01)        
        self.d_optimizer = tf.keras.optimizers.SGD(learning_rate=0.00001, clipnorm=0.01)
        self.g_optimizer = tf.keras.optimizers.SGD(learning_rate=0.00001, clipnorm=0.01)

    def gradient_penalty(self, real_data, fake_data):
        """ Calculates the gradient penalty.
        This loss is calculated on an interpolated sample
        and added to the discriminator loss.
        """
        # Get the interpolated sample
        real_data_shape = tf.shape(real_data)
        alpha = tf.random.normal(shape=[real_data_shape[0], real_data_shape[1], real_data_shape[2]], mean=0.0, stddev=2.0, dtype=tf.dtypes.float32)
        #alpha = tf.random_uniform([self.batch_size, 1], minval=-2, maxval=2, dtype=tf.dtypes.float32)
        interpolated = (alpha * real_data) + ((1 - alpha) * fake_data)

        with tf.GradientTape() as gp_tape:
            gp_tape.watch(interpolated)
            # 1. Get the discriminator output for this interpolated sample.
            pred = self.discriminator(interpolated, training=True)

        # 2. Calculate the gradients w.r.t to this interpolated sample.
        grads = gp_tape.gradient(pred, [interpolated])[0]
        # 3. Calculate the norm of the gradients.
        norm = tf.sqrt(tf.reduce_sum(tf.square(grads), axis=[-2, -1]))
        gp = tf.reduce_mean((norm - 1.0) ** 2)
        return gp    
        
    def encoder_loss(self,generated_fake_data, generator_reconstructed_encoded_fake_data):
        generator_reconstracted_data = tf.cast(generator_reconstructed_encoded_fake_data, tf.float32)
        loss = self.mse(generated_fake_data, generator_reconstracted_data)
        beta_cycle_gen = 10.0
        loss = loss * beta_cycle_gen
        return loss

    # Define the loss functions for the discriminator,
    # which should be (fake_loss - real_loss).
    # We will add the gradient penalty later to this loss function.
    def discriminator_loss(self, real_sample, fake_sample):
        real_loss = tf.reduce_mean(real_sample)
        fake_loss = tf.reduce_mean(fake_sample)
        return fake_loss - real_loss

    # Define the loss functions for the generator.
    def generator_loss(self, fake_sample):
        return -tf.reduce_mean(fake_sample)
    
    def compute_anomaly_score(self, input):
        """anomaly score.
          See https://arxiv.org/pdf/1905.11034.pdf for more details
        """
        # Encode the real data
        encoded_real_data = self.encoder(input, training=False)
        # Reconstruct encoded real data
        generator_reconstructed_encoded_real_data = self.generator(encoded_real_data, training=False)
        # Calculate distance between real and reconstructed data (Here may be step forward?)
        gen_rec_loss_predict = self.mse(input,generator_reconstructed_encoded_real_data)

        # # Compute anomaly score
        # real_to_orig_dist_predict = tf.math.reduce_sum(tf.math.pow(encoded_random_latent - encoded_real_data, 2), axis=[-1])
        # anomaly_score = (gen_rec_loss_predict * self.anomaly_alpha) + ((1 - self.anomaly_alpha) * real_to_orig_dist_predict)
        anomaly_score = gen_rec_loss_predict
        return {'anomaly_score': anomaly_score} 
    